

# scrolllock-wlroots-workaround
A workaround to activate Scroll Lock LED (the backlight in some keyboards) in wlroots based compositors.
 
~~According to this https://github.com/swaywm/sway/issues/5342#issuecomment-642287582, the LEDs appear to be updated [post-key-release regardless of the key](https://gitlab.freedesktop.org/wlroots/wlroots/-/blob/master/types/wlr_keyboard.c#L21-L34), which causes the backlight to be disabled immediately after turning it on.~~ **[LEDs now only update when a LED changes.](https://gitlab.freedesktop.org/wlroots/wlroots/-/merge_requests/3867)**. A workaround is still needed though.
 
If you are using GNOME/Mutter you can use these [workarounds](https://www.reddit.com/r/linuxquestions/comments/ruhse5/comment/hr0zbxj) in combination with the first workaround in this repo.

**Related issues and links:**

[Issue on Gitlab | Backlight activated by the Scroll Lock LED can't be turn on](https://gitlab.freedesktop.org/wlroots/wlroots/-/issues/3550)

[Merge request on Gitlab | types/wlr_keyboard.c : keyboard_led_update when leds is change (Merged) ](https://gitlab.freedesktop.org/wlroots/wlroots/-/merge_requests/3867)

[libinput/issue #11 | scrolllock, the only key that can switch keyboard back light can't be activated](https://gitlab.freedesktop.org/libinput/libinput/-/issues/11)

[libinput/issue #102 | Scroll Lock doesn't work as expected](https://gitlab.freedesktop.org/libinput/libinput/-/issues/102
)

[Reddit | I can't enable Scroll Lock to turn keyboard's LED lights [Devastador 2 Gaming Keyboard]](https://www.reddit.com/r/linuxquestions/comments/ruhse5/i_cant_enable_scroll_lock_to_turn_keyboards_led/)

## Workarounds

The python script workaround gives the same results as using `xset led named "Scroll Lock"` in Xorg, but requires executing a python script and executing it as ***root***. *This script should also work on GNOME/Mutter (untested).*

Since the second "workaround" got [merged]((https://gitlab.freedesktop.org/wlroots/wlroots/-/merge_requests/3867) ),  there's not need to patch wlroots anymore. I still recommend using the python script to prevent the <kbd>CapsLock</kbd> and <kbd>NumLock</kbd> from turning off the LED



## Workaround - Python script

Download it [here](https://github.com/bigrand/scrolllock-wlroots-workaround/blob/main/ledToggler.py "here").

Requires to run the script with admin-level access. (It reads from `/dev/input/event` and `/sys/class/leds/`)

This script is based on [libinput/examples/led-toggle.py](https://gitlab.freedesktop.org/libevdev/python-libevdev/-/blob/master/examples/led-toggle.py "libinput/examples/led-toggle.py")

### Dependencies
[`libevdev`](https://pypi.org/project/libevdev/ "`libevdev`")

### Execution steps

After installing the necessary packages and modules, and downloading the [script](https://github.com/bigrand/scrolllock-wlroots-workaround/blob/main/ledToggler.py "script"). You can proceed to execute it.

#### Usage
`python ledToggler.py <path> <keystr> <ledstr> <forceLed> <startLed>`

If you just want to enable your scroll lock LED use and toggle it as you want, then use:
`python ledToggler.py /dev/input/eventX scrolllock scrolllock 1 1` 

Replace `X` with your keyboard's handle event number. You can check it using:
[`cat /proc/bus/input/devices`](https://stackoverflow.com/q/6990978 "`cat /proc/bus/input/devices`")

#### Arguments/Options explanation
`<path>` refers to the event path of your keyboard. `dev/input/eventX`

`<keystr>` refers to the name of the toggle key. `numlock, capslock, scrolllock`

`<ledstr>` refers to the name of the LED that you want to toggle. `numlock, capslock, scrolllock`

`<forceLed>` when disabled it won't force the LED to stay on (susceptible to LEDs updates), when enabled it forces the LED to stay on unless the toggle key state is off. `0, 1`

**Important**: `<forceLed>` is useful to have it enabled because when <kbd>CapsLock</kbd> or <kbd>NumLock</kbd> are pressed, the <kbd>ScrollLock</kbd> LED turns off. When enabled, visually, the LED doesn't turn off.

`<startLed>` when disabled upon execution the script won't turn on the LED, when enabled upon execution the script will turn on the LED. `0, 1`

#### Commands to toggle the LED
You can use these commands to toggle the LED without the python script:
   
    brightnessctl --device='*::scrolllock' set 1 # ON
    brightnessctl --device='*::scrolllock' set 0 # OFF
    
    # Alternative
    sudo sh -c 'echo 1 > /sys/class/leds/inputX::scrolllock/brightness' # ON
    sudo sh -c 'echo 0 > /sys/class/leds/inputX::scrolllock/brightness' # OFF

You can also use these [workarounds to activate the LEDs](https://www.reddit.com/r/linuxquestions/comments/ruhse5/comment/hr0zbxj).

---

-  You can find the key event code/name of a key, using: `evtest`
 https://archlinux.org/packages/community/x86_64/evtest/

-  Another alternative to `evtest` is using `libevdev device example`
 https://python-libevdev.readthedocs.io/en/latest/examples.html#id1

- Replace X with the event handler number:
`cat /proc/bus/input/devices`


---
&nbsp;
## ~~#2 Workaround~~

**[This patch is merged!](https://gitlab.freedesktop.org/wlroots/wlroots/-/merge_requests/3867/diffs "This patch is merged! from 0.17.0 and on!")**

The Scroll Lock LED  will turn off when pressing <kbd>CapsLock</kbd> or <kbd>NumLock</kbd>, this can be "fixed" using the python script workaround and enabling the option `<forceLed>`.


### ~~Patching process~~

~~Clone `wlroots` and navigate to the `0.15.1` branch (change it to your installed version):~~

    git clone https://gitlab.freedesktop.org/wlroots/wlroots.git
    cd wlroots/
    git checkout 0.15.1  
    

 **~~Before building you have to replace `/wlroots/types/wlr_keyboard.c`~~** **~~with the patched [`wlr_keyboard.c`](https://gitlab.freedesktop.org/wlroots/wlroots/-/merge_requests/3867/diffs "`wlr_keyboard.c`").~~** **~~Be sure you are patching the correct file with the correct version, otherwise it wouldn't work. (You can patch it manually if the file and the wlroots version aren't the same).~~**

~~After patching `wlr_keyboard.c`, compile `wlroots`:~~

    meson -D examples=false build/
    ninja -C build/

~~Then replace your system's `libwlroots.so.10` with the patched one (the `libwlroots.so.` number could be different depending on the version of wlroots that you are compiling):~~

    strip build/libwlroots.so.10
    sudo cp -i build/libwlroots.so.10 /usr/lib/libwlroots.so.10

~~Restart Sway and now the LED shouldn't turn off on post-key-release.~~
