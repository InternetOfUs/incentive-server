#!/bin/bash
pushd /home/ubuntu/inc/backup

DB_DUMP_FILENAME=lassi.`date +%Y-%m-%d_%H-%M`.sql.gz
echo "Gonna create dump file: $DB_DUMP_FILENAME"

docker exec inc_db_1 mysqldump lassi -uroot -proot | gzip > $DB_DUMP_FILENAME

if [ $? -eq 0 ]; then
    echo "App database dump created OK. File: $DB_DUMP_FILENAME"
else
    echo "App database dump FAILED!"
    exit 1
fi

echo "Gonna upload dump file to S3: $DB_DUMP_FILENAME"


docker run --rm -v $(pwd):/project \
  -e "AWS_ACCESS_KEY_ID=AKIA3EOV67FLMENMPZEE" \
  -e "AWS_SECRET_ACCESS_KEY=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" \
  -e "AWS_DEFAULT_REGION=us-east-1" \
  mesosphere/aws-cli s3 cp /project/$DB_DUMP_FILENAME s3://wenet/$DB_DUMP_FILENAME

echo "Now remove dump file: $DB_DUMP_FILENAME"
rm -rf /home/ubuntu/sql_backup/$DB_DUMP_FILENAME

echo "Operation 1  Dump_and_Upload_lassi completed Successfully!"

DB_DUMP_FILENAME2=libraries.`date +%Y-%m-%d_%H-%M`.sql.gz
echo "Gonna create dump file: $DB_DUMP_FILENAME"

docker exec inc_db_1 mysqldump libraries -uroot -proot | gzip > $DB_DUMP_FILENAME2

if [ $? -eq 0 ]; then
    echo "App database dump created OK. File: $DB_DUMP_FILENAME"
else
    echo "App database dump FAILED!"
    exit 1
fi

echo "Gonna upload dump file to S3: $DB_DUMP_FILENAME"


docker run --rm -v $(pwd):/project \
  -e "AWS_ACCESS_KEY_ID=AKIA3EOV67FLMENMPZEE" \
  -e "AWS_SECRET_ACCESS_KEY=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" \
  -e "AWS_DEFAULT_REGION=us-east-1" \
  mesosphere/aws-cli s3 cp /project/$DB_DUMP_FILENAME2 s3://wenet/$DB_DUMP_FILENAME


echo "Now remove dump file: $DB_DUMP_FILENAME"
rm -rf /home/ubuntu/sql_backup/$DB_DUMP_FILENAME

echo "Operation 2  Dump_and_Upload_libraries completed Successfully!"

