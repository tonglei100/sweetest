from sweet import log

class Windows:

    def __init__(self):

        self.current_context = 'NATIVE_APP'

    def switch_context(self, context):
        if context.strip() == '':
            context = 'NATIVE_APP'
        if context != self.current_context:
            if context == '':
                context = None
            log.debug(f'switch context: {repr(context)}')
            self.driver.switch_to.context(context)
            self.current_context = context
