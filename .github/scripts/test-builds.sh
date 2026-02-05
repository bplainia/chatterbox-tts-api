#!/bin/bash
# Local Docker Build Test Script
# This script helps test Docker builds locally before pushing to GitHub

set -e

# Colors
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}🐳 Chatterbox TTS API - Local Docker Build Test${NC}"
echo "============================================================"

# Change to project root
cd "$(dirname "$0")/../.."

# Function to build and test an image
build_docker_image() {
    local name=$1
    local dockerfile=$2
    local tag=$3
    
    echo -e "\n${YELLOW}📦 Building: $name${NC}"
    echo "Dockerfile: $dockerfile"
    echo "Tag: $tag"
    echo "------------------------------------------------------------"
    
    local start_time=$(date +%s)
    
    if docker build -f "$dockerfile" -t "$tag" .; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        echo -e "${GREEN}✅ Build successful in ${duration} seconds${NC}"
        
        # Get image size
        local image_size=$(docker images "$tag" --format "{{.Size}}")
        echo -e "${CYAN}📊 Image size: $image_size${NC}"
        
        return 0
    else
        echo -e "${RED}❌ Build failed for $name${NC}"
        return 1
    fi
}

# Function to test an image
test_docker_image() {
    local name=$1
    local tag=$2
    local port=${3:-4123}
    
    echo -e "\n${YELLOW}🧪 Testing: $name${NC}"
    echo "------------------------------------------------------------"
    
    local container_name="test-$name"
    local success=0
    
    # Run the container
    echo "Starting container..."
    if docker run -d --name "$container_name" -p "${port}:4123" -e DEVICE=cpu "$tag"; then
        echo "Waiting for container to be ready..."
        
        local max_attempts=30
        local attempt=0
        local ready=false
        
        while [ $attempt -lt $max_attempts ]; do
            ((attempt++))
            sleep 2
            
            if curl -f http://localhost:${port}/health &>/dev/null; then
                ready=true
                break
            fi
            echo -n "."
        done
        
        echo ""
        
        if [ "$ready" = true ]; then
            echo -e "${GREEN}✅ Container is healthy!${NC}"
            
            # Show logs
            echo -e "\nContainer logs (last 10 lines):"
            docker logs "$container_name" --tail 10
            
            success=1
        else
            echo -e "${RED}❌ Container failed to become ready${NC}"
            echo -e "\nContainer logs:"
            docker logs "$container_name"
        fi
    else
        echo -e "${RED}❌ Failed to start container${NC}"
    fi
    
    # Cleanup
    echo -e "\nCleaning up..."
    docker stop "$container_name" &>/dev/null || true
    docker rm "$container_name" &>/dev/null || true
    
    return $((1 - success))
}

# Main execution
echo -e "\n${CYAN}🔨 Starting local builds...${NC}"

declare -a builds=(
    "standard:docker/Dockerfile:chatterbox-tts:test-standard"
    "cpu:docker/Dockerfile.cpu:chatterbox-tts:test-cpu"
    "uv:docker/Dockerfile.uv:chatterbox-tts:test-uv"
)

declare -A results_build
declare -A results_test

for build_spec in "${builds[@]}"; do
    IFS=':' read -r name dockerfile tag <<< "$build_spec"
    
    if build_docker_image "$name" "$dockerfile" "$tag"; then
        results_build[$name]="PASS"
        
        # Only test CPU and UV builds (they're faster)
        if [[ "$name" == "cpu" ]] || [[ "$name" == "uv" ]]; then
            if test_docker_image "$name" "$tag" 4123; then
                results_test[$name]="PASS"
            else
                results_test[$name]="FAIL"
            fi
        else
            results_test[$name]="SKIP"
            echo -e "${YELLOW}⏭️  Skipping test for $name (too slow for local testing)${NC}"
        fi
    else
        results_build[$name]="FAIL"
        results_test[$name]="SKIP"
    fi
done

# Summary
echo -e "\n${CYAN}============================================================${NC}"
echo -e "${CYAN}📊 Build Test Summary${NC}"
echo -e "${CYAN}============================================================${NC}"

all_passed=true

for build_spec in "${builds[@]}"; do
    IFS=':' read -r name dockerfile tag <<< "$build_spec"
    
    echo -e "\n${YELLOW}${name^^}${NC}"
    
    if [[ "${results_build[$name]}" == "PASS" ]]; then
        echo -e "  Build: ${GREEN}✅ PASS${NC}"
    else
        echo -e "  Build: ${RED}❌ FAIL${NC}"
        all_passed=false
    fi
    
    case "${results_test[$name]}" in
        "PASS")
            echo -e "  Test:  ${GREEN}✅ PASS${NC}"
            ;;
        "FAIL")
            echo -e "  Test:  ${RED}❌ FAIL${NC}"
            all_passed=false
            ;;
        "SKIP")
            echo -e "  Test:  ${YELLOW}⏭️  SKIP${NC}"
            ;;
    esac
done

echo -e "\n${CYAN}============================================================${NC}"

if [ "$all_passed" = true ]; then
    echo -e "${GREEN}🎉 All builds completed successfully!${NC}"
    echo -e "\n${CYAN}💡 You can now push to GitHub to trigger the CI/CD pipeline${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some builds failed. Please review the errors above.${NC}"
    exit 1
fi
