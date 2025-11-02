import aiohttp
import msgspec
from common.data.models import Problem, IPCheckResponse, IPInfoBasic


class IPApi:
    async def check_ips(self, ips_to_check: list[IPInfoBasic]) -> list[IPCheckResponse]:
        response_data: list[IPCheckResponse] = []
        async with aiohttp.ClientSession() as session:
            url = "http://ip-api.com/batch?fields=status,message,mobile,proxy,countryCode,region,city,as"
            # we can specify 100 IPs per request, so send requests in chunks of 100
            chunk_size = 100
            for i in range(0, len(ips_to_check), chunk_size):
                data = [ip.ip_address for ip in ips_to_check[i:i+chunk_size]]
                async with session.post(url, json=data) as resp:
                    if int(resp.status/100) != 2:
                        raise Problem("Error when sending request to IP site")
                    r = await resp.json()
                    body = msgspec.convert(r, type=list[IPCheckResponse])
                    # get ASNs since they are named "as" which we cannot put in a class name
                    for i in range(len(r)):
                        body[i].asn = r[i].get("as", None)
                    response_data.extend(body)
        return response_data