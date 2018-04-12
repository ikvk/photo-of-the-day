Add-Type @"
using System;
using System.Runtime.InteropServices;
using Microsoft.Win32;
public class Wallpaper {
   [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)]
   private static extern int SystemParametersInfo (int uAction, int uParam, string lpvParam, int fuWinIni);
   public static void SetWallpaper(string path) {
      SystemParametersInfo( 0x14, 0, path, 3 );
   }
}
"@

[void] [Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
[void] [Reflection.Assembly]::LoadWithPartialName("System.Drawing")
$Screens = [system.windows.forms.screen]::AllScreens

$wallpaper_url=("https://yandex.ru/images/today?size={0}x{1}" -f $Screens[0].Bounds.Width, $Screens[0].Bounds.Height)
$download_to= 'C:\Windows\Temp\wp.jpg'

Write-Output "I am setting wallpaper, do not close me =)"
Write-Output "$wallpaper_url"
Add-Type -Assembly System.Web | Out-Null
$wc = New-Object Net.WebClient
$wc.Encoding = [Text.Encoding]::UTF8
$wc.DownloadFile($wallpaper_url, $download_to)
[Wallpaper]::SetWallpaper($download_to)

Write-Output "Done."
Start-Sleep -s 3