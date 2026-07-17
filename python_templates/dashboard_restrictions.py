SUPPORTED_RESTRICTION_USERS = ['us', 'en_suite_room_user', 'guest_room_user']

EXEMPTION_USERS = [
  {"user": "72e8e305715145febff1ba701fd78954"}, # relliky
  {"user": "60652445f3d14a8f822054569404b643"}, # Ke
  {"user": "317c743e4c8348b8a70d671db917dbe8"}, # Tai
  {"user": "e9fbd5a00abd49b88122f03d68053128"}, # Guest room user
]


def restricted_access_card(user, inner_card):
  if user not in SUPPORTED_RESTRICTION_USERS:
    raise TypeError( "\n" +\
                     "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" + \
                     "User " + user + "is not supported for restriction card" + "\n" + \
                     "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")

  return {
    "type": "custom:restriction-card",
    "restrictions": {
      "hide": {
        "exemptions": EXEMPTION_USERS,
      }
    },
    "exemptions": EXEMPTION_USERS,
    "card": inner_card
  }
