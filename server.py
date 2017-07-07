from Siding.async_siding import Siding
import sys
import zerorpc

PORT = "4242"


def server():
  addr = 'tcp://127.0.0.1:' + PORT
  s = zerorpc.Server(Siding())
  s.bind(addr)
  print('start running on {}'.format(addr))
  s.run()

def main():
 server()

if __name__ == '__main__':
  main()