#!/bin/sh
set -e

awslocal s3 mb "s3://saeb-lambda-artifacts" || true
awslocal s3 mb "s3://saeb-student-reports" || true
awslocal s3 mb "s3://saeb-report-assets" || true