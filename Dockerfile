# 
# docker build -t bank-api:latest .
# docker save bank-api:latest | gzip -9 > ~/bank-api.tar.gz
# scp ~/bank-api.tar.gz maple@10.0.0.6:
# ssh maple@10.0.0.6
# gunzip -c ~/bank-api.tar.gz | docker load
# docker run -itd -p 5019:5000 --name bank-api --restart unless-stopped bank-api:latest
#
FROM python:3-onbuild

EXPOSE 5000

CMD [ "./api.sh" ]
