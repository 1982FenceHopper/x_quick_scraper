from twikit import Client, TooManyRequests
from twikit.tweet import Tweet
from twikit.list import Result
from typing import List, Any, Tuple
import pandas as pd
from datetime import datetime
import logging
import asyncio
import sys

class XComProvider():
    client: Client

    async def init(self, username: str, email: str, password: str) -> None:
        self.client = Client("en-US")

        await self.client.login(
            auth_info_1=username,
            auth_info_2=email,
            password=password,
            cookies_file="x_com_cookies.json",
            enable_ui_metrics=True
        )

    async def GetUserIDFromHandle(self, handle: str) -> str:
        return (await self.client.get_user_by_screen_name(screen_name=handle)).id
    
    async def ReturnInitialTweetsWithReplies(self, user_id: str, count: int = 20) -> Result[Tweet]:
        return await self.client.get_user_tweets(user_id=user_id, tweet_type="Tweets", count=count)

    async def ParseInitialTweetsWithRepliesAsJSON(self, tweet_object: Result[Tweet]) -> List[Any]:
        _tweet_list = []

        for tweet in tweet_object:
            all_replies = []
            if tweet.replies is not None:
                for reply in tweet.replies:
                    all_replies.append({
                        "uid": reply.user.id,
                        "username": reply.user.screen_name,
                        "tid": reply.id,
                        "content": reply.full_text,
                        "sent_on": reply.created_at
                    })

            _tweet_list.append({
                "uid": tweet.user.id,
                "username": tweet.user.screen_name,
                "tid": tweet.id,
                "content": tweet.full_text,
                "sent_on": tweet.created_at,
                "replies": all_replies
            })
        
        return _tweet_list
    
    async def HandleNextCursorForTweetsWithRepliesAsJSON(self, original_object: Result[Tweet]) -> Tuple[List[Any], Result[Tweet]]:
        _tweet_list = []

        _object = await original_object.next()

        if _object is None or _object.__len__() == 0:
            return ([], _object)

        for tweet in _object:
            all_replies = []
            if tweet.replies is not None:
                for reply in tweet.replies:
                    all_replies.append({
                        "uid": reply.user.id,
                        "username": reply.user.screen_name,
                        "tid": reply.id,
                        "content": reply.full_text,
                        "sent_on": reply.created_at
                    })

            _tweet_list.append({
                "uid": tweet.user.id,
                "username": tweet.user.screen_name,
                "tid": tweet.id,
                "content": tweet.full_text,
                "sent_on": tweet.created_at,
                "replies": all_replies
            })

        return (_tweet_list, _object)
    
    async def ReturnAllTweetsWithRepliesAsJSON(self, user_id: str, count: int = 20) -> List[Any]:
        logging.info("Invoking tweet list retrieval...")
        _initial_object = await self.ReturnInitialTweetsWithReplies(user_id=user_id, count=count)
        _initial_list = await self.ParseInitialTweetsWithRepliesAsJSON(tweet_object=_initial_object)

        final_list = _initial_list
        current_object = _initial_object
        total_count = len(final_list)
        retries = 0

        while current_object is not None and total_count < count:
            try:
                _result, _object = await self.HandleNextCursorForTweetsWithRepliesAsJSON(original_object=current_object)
                if len(_result) == 0:
                    break

                final_list.extend(_result)

                current_object = _object
                total_count = len(final_list)
                logging.info("List updated, Count: {c}/{t}".format(c=total_count, t=count))
            except TooManyRequests:
                logging.error("CAUTION: Rate Limit Reached")
                if retries < 3:
                    retries += 1
                    wait_time = 1 * 60
                    logging.warning("Retrying in {wt} minutes (Attempt {r}/3)".format(wt=wait_time, r=retries))
                    await asyncio.sleep(wait_time)
                else:
                    logging.error("Max attempts reached, stopping tweet retrieval and returning list as is...")
                    break
            except Exception as e:
                logging.error("Unknown error occured: {e}".format(e=e))
                sys.exit(1)

        return final_list
    
    async def ParseTweetObjectAsDataFrame(self, tweet_list: List[Any]) -> pd.DataFrame:
        dataframe = pd.DataFrame(columns=["uid", "username", "tid", "content", "sent_on", "ref_tid", "url"])

        for post in tweet_list:
            dataframe.loc[-1] = [post["uid"], post["username"], post["tid"], post["content"], post["sent_on"], "NA", "https://x.com/{u}/status/{tid}".format(u=post["username"], tid=post["tid"])]
            dataframe.index = dataframe.index + 1
            dataframe = dataframe.sort_index()
            for reply in post["replies"]:
                dataframe.loc[-1] = [reply["uid"], reply["username"], reply["tid"], reply["content"], reply["sent_on"], post["tid"], "https://x.com/{u}/status/{tid}".format(u=reply["username"], tid=reply["tid"])]
                dataframe.index = dataframe.index + 1
                dataframe = dataframe.sort_index()
        
        return dataframe
    
    async def DumpDataFrameAsCSV(self, df: pd.DataFrame, handle: str, outpath: str | None = None) -> None:
        current_tz = datetime.now().isoformat().replace(' ', '_').replace(":", "_").replace("-", "_").replace(".", "_")

        filepath = "output/{h}_{tz}.csv".format(h=handle, tz=current_tz) if outpath is None else outpath

        df.to_csv(filepath)
        logging.info("Dumped CSV to {fp}".format(fp=filepath))