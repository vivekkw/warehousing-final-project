mkdir deployment_package
cd deployment_package
#install the 3 required libraries in the directory
pip3 install --target=$(pwd) requests datetime mysql-connector-python
#lets get outside of the directory to include the lambda function in the folder
cd..
mv lambda_function.py deployment_package
#now we want to zip it all
zip -r my_deployment_package.zip deployment_package
