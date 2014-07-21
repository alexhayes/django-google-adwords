from django.core.exceptions import ValidationError as _ValidationError

class RateExceededError(Exception):

    def __init__(self, retry_after_seconds):
        self.retry_after_seconds = retry_after_seconds
        Exception.__init__(self, retry_after_seconds)

class ValidationError(_ValidationError):
    
    def __init__(self, field_name, message):
        self.field_name = field_name
        print 'Field error', self.field_name, message
        _ValidationError.__init__(self, message)
    
    def __str__(self):
        if hasattr(self, 'error_dict'):
            return repr(self.message_dict)
        return '%s for field %s' % (repr(self.messages), self.field_name)

    def __repr__(self):
        return 'Field %s caused ValidationError(%s)' % (self.field_name, self)