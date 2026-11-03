# Stage 1: Build & Dependency resolution using NVIDIA PyTorch/CUDA stack
FROM nvcr.io/nvidia/pytorch:23.08-py3 AS builder

WORKDIR /app

# Force CUDA extensions to build with proper target configurations
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime Production Image
FROM nvcr.io/nvidia/pytorch:23.08-py3

WORKDIR /app

# Expose required runtime target variables to ensure Triton/Modulus find hardware
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Copy over python package dependencies from builder stage
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy infrastructure files
COPY . .

EXPOSE 8000

# Fire up your main API Gateway framework
CMD ["python", "main_api_gateway.py"]
