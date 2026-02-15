Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$img = New-Object System.Drawing.Bitmap(
    [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width,
    [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height
)

$graphics = [System.Drawing.Graphics]::FromImage($img)
$graphics.CopyFromScreen(
    [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.X,
    [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Y,
    0, 0,
    $img.Size
)

$img.Save("c:\Users\colem\Code\blackglass-shard-alpha\blackglass_history_capture.png", [System.Drawing.Imaging.ImageFormat]::Png)
Write-Host "Screenshot Saved."
