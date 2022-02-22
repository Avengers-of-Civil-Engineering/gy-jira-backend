echo "TAG_VERSION = $TAG_VERSION"

docker build -t gy-jira-backend:$TAG_VERSION .
docker tag gy-jira-backend:$TAG_VERSION ccr.ccs.tencentyun.com/aweffr-main/gy-jira-backend:$TAG_VERSION
docker push ccr.ccs.tencentyun.com/aweffr-main/gy-jira-backend:$TAG_VERSION
