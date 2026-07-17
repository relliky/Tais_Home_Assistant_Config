import re


def get_prefix(entity):
  prefix = re.sub(r"\..*$", "", entity)

  if re.search(r'[\./!"£$%^&*()]', prefix) != None:
    raise ValueError("Prefix " + prefix + " still have specical characters $./!\"£$%^&*()")
  return prefix


def get_postfix(entity):
  postfix = re.sub(r"^.*\.", "", entity)

  if re.search(r'[\./!"£$%^&*()]', postfix) != None:
    raise ValueError("Postfix " + postfix + " still have specical characters $./!\"£$%^&*()")
  return postfix


def get_name_from_postfix(postfix):
  return re.sub("_", " ", postfix)


def captilize_sentence(s):
  return re.sub(r"(^|\s)(\S)", lambda m: m.group(1) + m.group(2).upper(), s)


def get_name_from_entity(entity):
  postfix = get_postfix(entity)
  name = get_name_from_postfix(postfix)
  return captilize_sentence(name)


def get_entity_from_name(text):
  text = text.lower()
  text = re.sub(r'[^\w]+', '_', text)
  text = re.sub("(_+)", "_", text)
  return text.strip('_')


def get_id_from_alias(alias):
  return "automation." + get_entity_from_name(alias)
