from starlette.requests import Request
from starlette.routing import Route
from api.data import handle
from api.utils.responses import JSONResponse
from common.data.commands import ReadFileInS3BucketCommand, WriteMessageToFileInS3BucketCommand

#@require_permission(permissions.READ_S3)
async def s3_read(request: Request) -> JSONResponse:
    try:
        bucket_name = request.query_params['bucket']
        file_name = request.query_params['file']

    except RuntimeError:
        return JSONResponse({'error': 'No correct body send'})

    body = await handle(ReadFileInS3BucketCommand(bucket_name, file_name))

    return JSONResponse({
        f'{bucket_name} - {file_name}':
        f'{body}'
    })

#@require_permission(permissions.WRITE_S3)
async def s3_write(request: Request) -> JSONResponse:
    try:
        bucket_name = request.query_params['bucket']
        file_name = request.query_params['file']
        message = request.query_params['message']
    except RuntimeError:
        return JSONResponse({'error': 'No correct body send'})

    message = message.encode('utf-8')

    await handle(WriteMessageToFileInS3BucketCommand(bucket_name, file_name, message))

    return JSONResponse({})

routes = [
    Route('/api/s3', s3_read),
    Route('/api/s3', s3_write, methods=["POST"]),
]