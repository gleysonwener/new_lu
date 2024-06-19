import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from dotenv import load_dotenv

load_dotenv()

# configuring sentry
sentry_sdk.init(
    dsn="https://7e3c537cc42659f5055f3523ca01c195@o4507461076647936.ingest.us.sentry.io/4507461079728128",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

def init_sentry(app):
    app.add_middleware(SentryAsgiMiddleware)
