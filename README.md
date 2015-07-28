# nowplaying.py
Tweets the tune now iTunes playing

## Dependency
- Mac OS X
- Appscript (Python module for Mac OS X)
  - iTunes
- lxml
- requests\_oauthlib
- bottlenose

## Configuration
Edit `config.json` before execution
```bash-session
$ cp config.json.sample config.json
```

Amazon product advertising API keys
[Amazon product advertising API](https://affiliate.amazon.co.jp/gp/advertising/api/detail/main.html)
- access_key
- secret_key
- assoc_tag

Twitter REST API authorization keys
[Twitter Developers](https://dev.twitter.com/)
- consumer_key
- consumer_secret
- access_token
- access_token_secret

## Usage

Run this program and Tweets automatically the music now playing in your iTunes.

Options are as follows

```
Usage: nowplaying.py [options] message

Options:
  -h, --help            show this help message and exit
  -q, --quiet           don't tweet and just display information for the song
                        now playing
  -r RATING, --rate=RATING
                        rate the song now playing
  -n, --no-amazon       don't search product in Amazon API
```

You can rate the song with `-r` option like `-r 5`

With `-q` option, this program doesn't tweet

```bash
$ python nowplaying.py -qr5 "Like it"
[Amazon search result]
THE VERY BEST OF EVERLASTING OLDIES volume1
<http://www.amazon.co.jp/dp/B00LPJVTYG/>

========================================================================
#NowPlaying
♪ Stand By Me − Ben E. King
（The Very Best Of Everlasting Oldies）
★★★★★
http://www.amazon.co.jp/dp/B00LPJVTYG/

Like it
========================================================================
```

## Customize

You can modify `config.json` to change formats of NowPlaying.

### Format for Tweet text

| formatting option | description                   |
|:------------------|:------------------------------|
|title              |Title of the song              |
|artist             |Artist of the song             |
|album              |Album title                    |
|rating             |Rating (if larger than one)    |
|comment            |Comment from argument          |
|url                |URL for Amazon product         |
|product            |Amazon product name            |


