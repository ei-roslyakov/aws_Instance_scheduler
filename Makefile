FUNC_NAME					= instance-switcher-func

.PHONY: help
help:
	@echo "make build        # build lambda function"

.PHONY: build
build:
	cd lambda_package && pip3 install -r ../requirements.txt --target ./package
	cd lambda_package/package && zip -r ../$(FUNC_NAME).zip .
	zip lambda_package/$(FUNC_NAME).zip lambda.py
