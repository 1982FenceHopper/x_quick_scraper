import asyncio
from .utils import XComProvider
from dotenv import load_dotenv
import os, sys
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format="[%(asctime)s - %(levelname)s] %(message)s")

async def main():
    global user_opts
    user_opts = None

    try:
        with open("_users.txt", "r", encoding="utf-8") as fd:
            user_opts = fd.read()
    except FileNotFoundError:
        print("No _users.txt file found.")
        sys.exit(1)

    user_opts = user_opts.strip().split("\n")

    provider = XComProvider()
    await provider.init(
        username=os.environ["USERNAME"],
        email=os.environ["EMAIL"],
        password=os.environ["PASSWORD"]
    )

    os.makedirs("output/", exist_ok=True)

    for account in user_opts:
        clean_account = account.strip()
        split = clean_account.split(":")

        handle = split[0]
        count = int(split[1])

        user_id = await provider.GetUserIDFromHandle(handle=handle)
        
        tweets_list = await provider.ReturnAllTweetsWithRepliesAsJSON(user_id=user_id, count=count)

        df = await provider.ParseTweetObjectAsDataFrame(tweet_list=tweets_list)
        await provider.DumpDataFrameAsCSV(df=df, handle=handle)

if __name__ == "__main__":
    asyncio.run(main())