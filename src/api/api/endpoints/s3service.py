import aiobotocore.session
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from api.auth import permissions, require_permission
from api.s3 import create_s3_client

@require_permission(permissions.READ_S3)
async def s3_read(request: Request) -> JSONResponse:
    try:
        bucket_name = request.query_params['bucket']
        file_name = request.query_params['file']

    except RuntimeError:
        return JSONResponse({'error': 'No correct body send'})

    session = aiobotocore.session.get_session()
    async with create_s3_client(session) as s3_client:
        response = await s3_client.get_object(Bucket=bucket_name, Key=file_name)
        async with response['Body'] as stream:
            body = await stream.read()

    return JSONResponse({
        f'{bucket_name} - {file_name}':
        f'{body}'
    })

@require_permission(permissions.WRITE_S3)
async def s3_write(request: Request) -> JSONResponse:
    try:
        bucket_name = request.query_params['bucket']
        file_name = request.query_params['file']
        message = request.query_params['message']
    except RuntimeError:
        return JSONResponse({'error': 'No correct body send'})

    message = message.encode('utf-8')

    session = aiobotocore.session.get_session()
    async with create_s3_client(session) as s3_client:
        result = await s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=message)

    return JSONResponse(result)

routes = [
    Route('/api/s3', s3_read),
    Route('/api/s3', s3_write, methods=["POST"]),
]