class BasicProbe(object):
    
    

    def probe(self, value):
        """Probe the value:
    
        * increase found value count
        * identify storage type
        * probe for null and for empty string

        * probe distinct values: if their count is less than ``distinct_threshold``. If there are more
          distinct values than the ``distinct_threshold``, then distinct_overflow flag is set and list
          of distinct values will be empty
                
        """
    
        storage_type = value.__class__
        self.storage_types.add(storage_type.__name__)

        self.value_count += 1
    
        # FIXME: check for existence in field.empty_values
        if value is None:
            self.null_count += 1

        if value == '':
            self.empty_string_count += 1

        self._probe_distinct(value)
    
        for probe in self.probes:
            probe.probe(value)
