import argparse


def build_arg_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument('-R', dest ='render_auto_config', default=True,
                      action ='store_false', help ='Skip rendering auto-generated yaml config')
  parser.add_argument('-C', dest ='check_auto_system_config', default=True,
                      action ='store_false', help ='Skip checking on unexpected entities in the system file core.entity_entries')
  parser.add_argument('-c', dest ='create_system_config', default=False,
                      action ='store_true', help ='Create a system file core.entity_entries that removes unexpected entities')
  parser.add_argument('-d', '-dy', '-dyaml', dest ='render_dashboard_yaml', default=False,
                      action ='store_true', help ='Render lovelace config files to YAML format. Default to false as it takes extra time and lovelace are not updated often')
  parser.add_argument('-dj', '-djson', dest ='render_dashboard_json', default=False,
                      action ='store_true', help ='Render lovelace config files to JSON format. Default to false as it takes extra time and lovelace are not updated often')
  parser.add_argument('-dm', '-dmobile', dest ='render_dashboard_mobile', default=False,
                      action ='store_true', help ='Render mobile dashboard. Default to false as it takes extra time and lovelace are not updated often')
  parser.add_argument('-dt', '-dtablet', dest ='render_dashboard_tablet', default=False,
                      action ='store_true', help ='Render tablet dashboard. Default to false as it takes extra time and lovelace are not updated often')
  parser.add_argument('-lc', '-language-chinese', dest='dashboard_language_chinese', default=False,
                      action ='store_true', help ='Render dashboard in Chinese. Default to false as it takes extra time and lovelace are not updated often')

  return parser


def parse_args(argv=None):
  return build_arg_parser().parse_args(argv)


def get_dashboard_type(parsed_args):
  return 'tablet' if parsed_args.render_dashboard_tablet is True else \
         'mobile' if parsed_args.render_dashboard_mobile is True else \
         'default'


def get_dashboard_language(parsed_args):
  return 'Chinese' if parsed_args.dashboard_language_chinese is True else \
         'English'
