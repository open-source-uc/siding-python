from colorama import init, Fore

init()

colors = {'normal': (Fore.RESET,),
          'alert': (Fore.RED,),
          'success': (Fore.GREEN,),
          'result': (Fore.YELLOW,)}

def cool_print(*args, style='normal', **kwargs):
    print(*colors[style], end="")
    print(*args, **kwargs)
    print(*colors['normal'], end="")

    if style == 'alert':
        with open('alerts.log', 'a') as f:
            f.write(repr(args))
            f.write("\n")
            