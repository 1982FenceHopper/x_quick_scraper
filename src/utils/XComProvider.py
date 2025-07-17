from twikit import Client
from typing import List, Any
import pandas as pd
from datetime import datetime

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

    async def ReturnAllTweetsWithRepliesAsJSON(self, user_id: str, count: int = 20) -> List[Any]:
        _tweet_list = []

        tweets = await self.client.get_user_tweets(user_id=user_id, tweet_type="Tweets", count=count)

        for tweet in tweets:
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
    
    async def DumpDataFrameAsCSV(self, df: pd.DataFrame, outpath: str | None = None) -> None:
        current_tz = datetime.now().isoformat().replace(' ', '_').replace(":", "_").replace("-", "_").replace(".", "_")

        filepath = "df_dump_{tz}.csv".format(tz=current_tz) if outpath is None else outpath

        df.to_csv(filepath)