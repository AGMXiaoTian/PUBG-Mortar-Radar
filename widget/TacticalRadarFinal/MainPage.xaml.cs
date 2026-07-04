using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;
using Windows.Data.Json;
using System;
using Microsoft.Gaming.XboxGameBar;
using Windows.UI.Xaml.Navigation;
using Windows.Storage;
using System.IO;

namespace TacticalRadarFinal
{
    public sealed partial class MainPage : Page
    {
        private XboxGameBarWidget widget;
        private DispatcherTimer timer;

        public MainPage()
        {
            this.InitializeComponent();

            var localSettings = ApplicationData.Current.LocalSettings;
            if (localSettings.Values["IsVertical"] is bool isVert && isVert)
            {
                DataStack.Orientation = Orientation.Vertical;
            }
            else
            {
                DataStack.Orientation = Orientation.Horizontal;
            }

            timer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(50) };
            timer.Tick += FetchDataFromPython;
            timer.Start();
        }

        protected override void OnNavigatedTo(NavigationEventArgs e)
        {
            widget = e.Parameter as XboxGameBarWidget;
        }

        private void ToggleLayout_Click(object sender, RoutedEventArgs e)
        {
            DataStack.Orientation = DataStack.Orientation == Orientation.Horizontal ? Orientation.Vertical : Orientation.Horizontal;
            ApplicationData.Current.LocalSettings.Values["IsVertical"] = (DataStack.Orientation == Orientation.Vertical);
        }

        private async void FetchDataFromPython(object sender, object e)
        {
            if (widget != null)
            {
                bool isForeground = (widget.GameBarDisplayMode == XboxGameBarDisplayMode.Foreground);
                LayoutBtn.Opacity = isForeground ? 1.0 : 0.0;
                LayoutBtn.IsHitTestVisible = isForeground;
            }

            try
            {
                StorageFolder localFolder = ApplicationData.Current.LocalFolder;
                StorageFile file = await localFolder.GetFileAsync("radar_data.json");

                string jsonStr;
                using (Stream stream = await file.OpenStreamForReadAsync())
                using (StreamReader reader = new StreamReader(stream))
                {
                    jsonStr = await reader.ReadToEndAsync();
                }

                JsonObject data = JsonObject.Parse(jsonStr);

                // 1. 解析常规 4 个距离
                if (data.ContainsKey("distances"))
                {
                    JsonArray distances = data.GetNamedArray("distances");
                    DistYellow.Text = distances[0].GetString();
                    DistRed.Text = distances[1].GetString();
                    DistBlue.Text = distances[2].GetString();
                    DistGreen.Text = distances[3].GetString();
                }

                // 2. 【核心修复】：极度安全的解析手动测距文本，防止崩溃
                if (data.ContainsKey("manual_dist"))
                {
                    IJsonValue manualDistVal = data.GetNamedValue("manual_dist");
                    if (manualDistVal.ValueType == JsonValueType.String)
                    {
                        string manualText = manualDistVal.GetString();
                        if (!string.IsNullOrEmpty(manualText))
                        {
                            ManualDistText.Text = manualText;
                            ManualDistText.Visibility = Visibility.Visible;
                        }
                        else
                        {
                            ManualDistText.Visibility = Visibility.Collapsed;
                        }
                    }
                }
                else
                {
                    ManualDistText.Visibility = Visibility.Collapsed;
                }
            }
            catch { } // 发生任何读写冲突，静默跳过
        }
    }
}