import pandas as pd
from twscrape.logger import set_log_level

set_log_level("DEBUG")


async def setup_accounts(api):
    cookies = "abc=12; ct0=xyz"
    # Exemple de la documentació. Jo sempre he fet sevir pass3 == mail_pass3 i sembla funcionar
    await api.pool.add_account("user3", "pass3", "u3@mail.com", "mail_pass3", cookies=cookies)
    await api.pool.login_all()


def tweets2df(tweets, parse_tweet):
    parsed_data = []
    for tweet in tweets:
        tweet_data = parse_tweet(tweet)
        parsed_data.append(tweet_data)
    df = pd.DataFrame(parsed_data)
    return df
