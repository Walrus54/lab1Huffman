from collections import defaultdict
from heapq import heappush, heappop
import filecmp

class Node:
    def __init__(self, char, freq, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

def read_input(filename):
    with open(filename, "rb") as code_txt:
        return code_txt.read()

def load_data(filename):
    with open(filename, "rb") as file:
        codes_len = int.from_bytes(file.read(2), byteorder='big')
        padding = int.from_bytes(file.read(2), byteorder='big')
        huffman_codes = {}

        for _ in range(codes_len):
            byte = int.from_bytes(file.read(1), byteorder='big')
            code_len = int.from_bytes(file.read(1), byteorder='big')
            int_code = int.from_bytes(file.read(4), byteorder='big')
            code = bin(int_code)[2:].rjust(code_len, '0')
            huffman_codes[byte] = code

        data_bits = file.read()
        encoded_text = ''.join([bin(byte)[2:].rjust(8, '0') for byte in data_bits])

    return huffman_codes, encoded_text, padding

def save_data(huffman_codes, encoded_text, padding):
    with open("encoded.txt", "wb") as encoded_file:
        encoded_file.write(len(huffman_codes).to_bytes(2, byteorder='big'))
        encoded_file.write(padding.to_bytes(2, byteorder='big'))

        for byte, code in huffman_codes.items():
            encoded_file.write(bytes([byte]))
            encoded_file.write(len(code).to_bytes(1, byteorder='big'))
            encoded_file.write(int(code, 2).to_bytes(4, byteorder='big'))

        encoded_bytes = bytes(int(encoded_text[i:i+8], 2) for i in range(0, len(encoded_text), 8))
        encoded_file.write(encoded_bytes)

def encode(root, code="", huffman_code=None):
    if huffman_code is None:
        huffman_code = {}
    if root is None:
        return
    if root.char != '\0':
        huffman_code[root.char] = code
    encode(root.left, code + "0", huffman_code)
    encode(root.right, code + "1", huffman_code)
    return huffman_code

def decode(code_dict, encoded_string, index=0):
    decoded_string = bytearray()
    current_code = ''
    while index < len(encoded_string):
        current_code += encoded_string[index]
        if current_code in code_dict.values():
            for symbol, code in code_dict.items():
                if code == current_code:
                    decoded_string.append(symbol)
                    current_code = ''
                    break
        index += 1
    return decoded_string

def build_huffman_tree(byte_string):
  freq = defaultdict(int)
  for byte in byte_string:
    freq[byte] += 1
  priority_queue = []
  for byte, count in freq.items():
    heappush(priority_queue, Node(byte, count))
  while len(priority_queue) > 1:
    left = heappop(priority_queue)
    right = heappop(priority_queue)
    sum_freq = left.freq + right.freq
    heappush(priority_queue, Node('\0', sum_freq, left, right))
  root = heappop(priority_queue)
  return root

def main():
  while True:
    mode = input("Choose mode (encode(1)/decode(2)/exit(3)): ")
    if mode == "1":
      text = read_input("input.txt")+bytes([65])
      root = build_huffman_tree(text)
      huffman_code = encode(root)
      encoded_string = "".join(huffman_code[byte] for byte in text)
      padding = 8 - len(encoded_string) % 8
      save_data(huffman_code, encoded_string, padding)
      print("Encoded string written to encoded.txt")
    elif mode == "2":
      loaded_huffman_codes, loaded_encoded_text, loaded_padding = load_data("encoded.txt")
      loaded_encoded_text = loaded_encoded_text[:-loaded_padding]
      decode_text = (decode(loaded_huffman_codes, loaded_encoded_text))[:-1]   
      with open("decoded.txt", "wb") as decoded_file:
        decoded_file.write(decode_text)
      print("Decoded string written to decoded.txt")
      print(filecmp.cmp("input.txt", "decoded.txt", shallow=True))
    elif mode == "3":
      break
    else:
      print("Invalid mode. Please choose 'encode(1)', 'decode(2)', or 'exit(3)'.")

if __name__ == "__main__":
  main()