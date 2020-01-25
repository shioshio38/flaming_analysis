# twitter 炎上調査

# 概要

このアプリは、twitter上の炎上tweetを取得し、そのtweetが批判、中立、容認のどれなのかを調べるためのプログラムだ。

このプログラムは２つの部分からなっている。

1. tweetをフェッチするプログラム
1. 取得したプログラムを批判、中立、容認に仕分けるプログラム

である。

# 必要ミドルウェア

[`mongo`](https://www.mongodb.com/)

mongo上に、dataの保存を行っている。

mongoは、ユーザー認証を設定する。 [参考](https://qiita.com/h6591/items/68a1ec445391be451d0d)

# 各種設定

`.env.sample` を参考に、`.env` ファイルを作る。

```
MONGO_HOST=(MONGOホスト)
MONGO_USER=ユーザー認証したユーザー
PASSWORD=MONGOのパスワード
AUTHSOURCE=MONGOのauthsource
SECRET_KEY=Flaskで使うsession key
MONGO_DB=tweetを取得する際のDB
COLLECTION=tweetを取得するコレクション
access_token=twitterの提供した認証キー
access_token_secret=twitterの提供した認証キー
consumer_key=twitterの提供した認証キー
consumer_key_secret=twitterの提供した認証キー
```

# 必要なpythonライブラリの取得

必要なpythonライブラリは、`requirements.txt` を用意しているので一括で取得できる。

`pip3 install -r requirements.txt`

# tweetを取得する。

tweetを取得するにはtwitterに開発者登録する必要がある。こちらを[参考](https://dev.classmethod.jp/etc/twitter-developer/)

開発者登録をして、 `access_token`,`access_token_secret`,`consumer_key`,`consumer_key_secret`を取得する。
`.env.sample` ファイルを参考に、`.env` ファイルを作る。
mongoへ保存するため、`MONGO_HOST` などを指定する。

`get_tweet.py`の関数 `get_tw()` 内の、`query` と `until` をほしい項目と期間を指定する。`until` までの7日間データが取れる。

```
query=u'"猿" OR "雉"' # 猿と雉を含むtweetを検索する。 AND,ORを使える（小文字ではなく大文字で指定する）
until=datetime(2020,1,21) #取得したい期間を指定する。(この日まで、７日間を指定する)
```

# 取得したtweetを表示するため、サーバを立ち上げる。

```
python3 srv.py
```
でポート5000で立ち上がる。


