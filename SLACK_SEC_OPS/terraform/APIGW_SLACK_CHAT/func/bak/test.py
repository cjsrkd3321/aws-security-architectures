# import asyncio


# async def get_logs(regions=["ap-northeast-1", "us-east-1", "asdf", "c", "v"]):
#     msg = ""
#     done, pending = await asyncio.wait(
#         [asyncio.create_task(lookup_events(region)) for region in regions]
#     )
#     for d in done:
#         msg += d.result()

#     return msg


# async def lookup_events(region="ap-northeast-1"):
#     # print(region)
#     return region


# print(asyncio.run(get_logs()))
