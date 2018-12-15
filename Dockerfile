# 
# docker build -t jemvote:latest .
# docker run -itd -p 5000:5000 --name jemvote --restart unless-stopped jemvote:latest
#
FROM python:3-onbuild

EXPOSE 5000

CMD [ "./api.sh" ]
