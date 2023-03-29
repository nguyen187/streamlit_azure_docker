from python:3.9.0
expose 8501
cmd mkdir -p /app
WORKDIR /app
copy . .
run pip3 install -r requirements.txt
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    python3-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17


ENTRYPOINT [ "streamlit","run" ]
CMD ["_🏡_Home.py"]