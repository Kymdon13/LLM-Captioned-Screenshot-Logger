# Introduction

This is a logger of your work on screen.

The logger will capture your screen and send the screenshot to your ollama server to generate description of the screenshot, and after an interval (like 24h) the logger will send you an email about what you did in the past day.

# Guide

### Ollama

To use the scripts, you have to install ollama on your PC and pull the following models:

```bash
qwen2.5vl:latest           5ced39dfa4ba    6.0 GB
qwen3:8b                   500a1f067a9f    5.2 GB
```

and to pull models, you just run:

```bash
ollama pull qwen3:8b
ollama pull qwen2.5vl:latest
```

after pulling all the models we need, just run:

```bash
ollama serve
```

to start the ollama server, the server will listen on localhost:11434 by default.

If you run the ollama server on remote you need to configure the ssh tunnel:

```bash
ssh -L localhost:11434:localhost:11434 user_name@ip.of.remote.machine -N
```

then you will be able to access the api of ollama on localhost.

### Python venv

I use *uv* to configure my python virtual environment, install *uv* first and run:

```bash
uv sync
```

to sync to my venv, uv will read the `pyproject.toml` file in the project dir and sync the venv.

### Email

You would have to configure the email on your remote machine so it can be able to send you an email of your daily activity, you must fill in 3 fields in email_sender.py:

```python
sender_email='',
sender_password='',
receiver_email=''
```

### Enjoy

After configuring the environment, you can run:

```bash
python main.py
```

to start logging yourself, but before you start doing so, you better set the timedelta to 1h or so in `Timestamp.is_past_a_day()` to see if there is any bug.
