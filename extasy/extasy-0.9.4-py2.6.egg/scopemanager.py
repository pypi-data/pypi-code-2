class _Scope( object ):
    stack = []

    def reset( self ):
        self.stack = []
        
    def get_xpath( self ):
        if not self.stack:
            return ''
        
        return self.stack[ -1 ][ 1 ]

    def enter( self, scope_xpath, indentation_level ):
        if self.stack and self.stack[ -1 ] == indentation_level:
            return

        self.stack.append( ( indentation_level, scope_xpath, ) )

    def quit_to_indentation_level( self, indentation_level ):
        i = 0
        while self.stack:
            if self.stack[-1][0] <= indentation_level:
                break

            i += 1
            self.stack.pop()
            
scope = _Scope()