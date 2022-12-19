#!/bin/bash

echo "Creating layer compatible with python version 3.9"
docker run --platform linux/amd64 -v "$PWD":/var/task "public.ecr.aws/sam/build-python3.9" /bin/sh -c "pip install -r requirements.txt -t python/; exit"
zip -r python.zip python > /dev/null
rm -r python
echo "Done creating layer!"
ls -lah python.zip