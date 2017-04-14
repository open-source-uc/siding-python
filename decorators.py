def check(*args):
    def check_arguments(function):
        def wrapper(*fargs):
            print(args, fargs)
            if not(all( 
                ( x == None
                  or (isinstance(y, x[0])
                  and (len(x) == 1 or y in x[1]
                ))) for x, y in zip(args, fargs))):

                raise TypeError("Los argumentos de la funcion no hacen match")
            return function(*fargs)
        return wrapper
    return check_arguments


@check((str,), (int, [1, 2, 3]))
def foo(str1, int):
    print(str1)


def main():
    foo("hola", 3)


if __name__ == '__main__':
    main()
