def is_delete(root):
    """
    Check if the operation is a delete. If there's no operation, or
    the indicated operation is not delete, return FALSE.
    """
    for x in root.iter('{urn:ietf:params:xml:ns:yang:ietf-yang-patch}operation'):
        if x.text == 'delete':
            return True
    return False
