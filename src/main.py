import asyncio
from .utils import XComProvider
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    provider = XComProvider()
    await provider.init(
        username=os.environ["USERNAME"],
        email=os.environ["EMAIL"],
        password=os.environ["PASSWORD"]
    )

    user_id = await provider.GetUserIDFromHandle(handle="AbuLocation")
    tweets_object = await provider.ReturnAllTweetsWithRepliesAsJSON(user_id=user_id, count=100)
    df = await provider.ParseTweetObjectAsDataFrame(tweet_list=tweets_object)
    await provider.DumpDataFrameAsCSV(df=df)

if __name__ == "__main__":
    asyncio.run(main())