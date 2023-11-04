from json import dumps

class Response:
    status=None
    message=None
    data=None
    
    _returned=None
    _bytes=None
    _offset=None
    _chunk=None

    def __init__(self):
        self.status=None
        self.message=None
        self.data={}

    def __str__(self):
        msg={}
        msg['status']=self.status        
        msg['message']=self.message
        msg['data']=self.data

        return dumps(msg,ensure_ascii=True)
        
    def __bytes__(self):
        return self.__str__().encode('utf-8')

    def __iter__(self):
        self._offset=0
        self._chunk=1024*100

        self._bytes=self.__bytes__()

        return self

    def __next__(self):
        if self._returned:
            raise StopIteration

        data=self._bytes[self._offset:self._offset+self._chunk]
        if len(data)<self._chunk:
            self._returned=True
        else:
            self._offset+=self._chunk

        return data