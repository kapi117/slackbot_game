# SlackBot for game for EESTEC members

As a part of internal EESTEC game, aimed to give fun, learn new things and make people engaged with Hacknarok, we created a game bot for Slack. This bot is used to give tasks, check if they are done, give points and so on.

# Initial configuration of bot

1. Go into _Manage Apps_, in the top left corner click _Build_
2. Click _Create New App_
3. Fill in the name of the app and select the workspace
4. Go to _OAuth & Permissions_ and add the following scopes:
   - app_mentions:read
   - channels:history
   - channels:read
   - chat:write
   - chat:write.customize
   - emoji:read
   - files:read
   - files:write
   - im:history
   - im:read
   - im:write
   - reactions:read
   - reactions:write
   - channels:read
   - users:read
   - users:write
5. Go to _Socket Mode_ and enable it
6. Go to _App Home_ and set nice _Default Name_, tick _Allow users to send Slash commands and messages from the messages tab_, enable _Home Tab_
7. Go to _Incoming Webhooks_ and enable it, then click _Add New Webhook to Workspace_
8. If channel you want to post in via webhook is not created, create one and choose it
9. Go to _Event Subscriptions_ and enable it
10. Add the following events:
    - app_mention
    - message.im
    - member_joined_channel
    - reaction_added
    - message.channels
    - app_home_opened
11. Go to _Basic Information_ and customize _Display Information_
12. Go to _Install App_ and install the app to your workspace
13. Create a file called `.env` in the root directory of the project
14. Insert to this file tokens:
    - `BOT_TOKEN` - token from _Install App_, starting from xoxb
    - `APP_TOKEN` - token from _Basic Informaation_ > _Tokens_, starting from xapp
