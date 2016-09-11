import curses
import logging

from functools import partial

from hst.hst import Picker, QuitException


logger = logging.getLogger(__name__)
SEPARATOR = '|'


class SimpleLineLoader(object):
    def __init__(self, client, region=None, tags=None):
        self.client = client
        self.region = region
        self.tags = tags
        self.footer = 'type something to search | [F5] copy | [TAB] complete to current | [ENTER] run | [ESC] quit'
        self.get_instances()

    def get_instances(self):
        self.instances = self.client.get_instances(self.region, tags=self.tags)

    def load(self):
        lines = []
        for i in self.instances:
            name = [tag['Value'] for tag in i.tags if tag['Key'] == 'Name'][0]
            line = []
            ip = i.public_ip_address or i.private_ip_address
            line.append(name.ljust(50))
            line.append(' | ')
            line.append(ip.ljust(16))
            line.append(' | ')
            line.append('{}'.format(i.key_name).ljust(30))
            line.append(' | ')
            line.append('{}'.format(i.id))
            lines.append(' '.join(line))

        return lines

class BasePicker(Picker):

    client = None
    output_only = False

    def get_data_from_line(self, line, nat_data=True):
        instance_id = line.split(SEPARATOR)[-1].strip()
        instance = self.client.get_instance(instance_id)
        ip = instance.public_ip_address or instance.private_ip_address
        if nat_data:
            nat_ip, nat_key = self.client.get_nat(instance)
        else:
            nat_ip, nat_key = None, None
        return {'ip': ip,
                'instance_id': instance_id,
                'nat_ip': nat_ip,
                'nat_key': nat_key,
                'key_name': instance.key_name,
                'tags': instance.tags}

    def get_cmd_fn_from_modules(self, *modules):
        for module in modules:
            fn = getattr(module, 'cmd_{}'.format(self.args.command.upper()), None)
            if fn:
                return fn

    def get_cmd_fn(self, cmd_name):
        from . import commands
        fn = self.get_cmd_fn_from_modules(self.settings, commands)
        if fn:
            return partial(fn, self)

        # look for builtins
        return getattr(self, 'cmd_{}'.format(self.args.command.upper()))

    def write_output(self, line):
        with open(self.args.out, 'w') as f:
            if self.output_only:
                out = '''cat <<'HereDocFromASSH' \n %s \nHereDocFromASSH\n\n''' % line
                f.write(out.encode('utf8'))
            else:
                f.write(line.encode('utf8'))

    def show_output(self, t):
        self.output_only = t

    def create_menu(self):
        self.win.addstr(3, 10, "xxxxxxxxxxx", curses.color_pair(1))
        for i in range(0, 10):
            self.win.addstr(4 + i, 10, "x    {}     x".format(i), curses.color_pair(1))
        self.win.addstr(4 + 10, 10, "xxxxxxxxxxx", curses.color_pair(1))

    def refresh_window(self, pressed_key=None):
        self.lineno = 0
        if pressed_key:
            self.search_txt = self.append_after_cursor(self.search_txt, pressed_key)

        # curses.endwin()
        self.win.erase()

        self.print_header(self.search_txt, cursor=True)

        logger.debug("======================== refresh window ======================")
        self.which_lines(self.search_txt)

        if not self.last_lines:
            self.print_line("Results [{}]".format(self.index.size()), highlight=True)
        else:
            self.print_line("Results - [{}]".format(len(self.last_lines)), highlight=True)

        max_y, max_x = self.get_max_viewport()

        if self.selected_lineno > len(self.which_lines(self.search_txt)) - 1:
            self.selected_lineno = len(self.which_lines(self.search_txt)) - 1

        logger.debug("self.multiple selected %s", self.multiple_selected)

        for i, p in enumerate(self.last_lines[0:max_y]):
            selected = i == self.selected_lineno
            pending = (self.pick_line(i) in self.multiple_selected)
            logger.debug("is pending %s [%s____%s]", pending, self.pick_line(i), self.multiple_selected)
            try:
                if pending:
                    line = u"[x] {}".format(p[1])
                else:
                    line = u"[ ] {}".format(p[1])
            except:
                logger.exception("exception in adding line %s", p)
            else:
                try:
                    self.print_line(line.strip(), highlight=selected, semi_highlight=pending)
                except curses.error:
                    break

        # self.create_menu()

        try:
            self.print_footer("[%s] %s" % (self.mode, self.footer))
        except curses.error as e:
            pass
        self.win.refresh()


    def key_DOWN(self):
        max_y, max_x = self.get_max_viewport()

        if self.selected_lineno < max_y - 1:
            self.selected_lineno += 1

        self.refresh_window()
