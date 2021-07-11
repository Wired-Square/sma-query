# SMA Sunny Boy Inverter Query Tool

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

The SMA Sunny Boy Inverter Query tool uses the SpeedWire™ protocol to query models of SunnyBoy inverter that support the protocol. The protocol was primarily decoded from analysis and replay of commands extracted from network dumps.

Some critical information regarding login was found in this post https://community.openhab.org/t/example-on-how-to-access-data-of-a-sunny-boy-sma-solar-inverter/50963 on the openHAP forum. Thank you to jan_r and all contributors to that thread!

This library supports a stand-alone MQTT mode, however, it is primarily intended to be used with Home Assistant.

