import slack
import slack.webhook

client = slack.webhook.WebhookClient('https://hooks.slack.com/services/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')
client.send(text='Hello, world!')
