using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;
using Windows.UI.Xaml.Shapes;
using Windows.UI.Xaml.Media;
using Windows.UI;
using Windows.UI.Text;
using System;
using Windows.Data.Json;
using Microsoft.Gaming.XboxGameBar;
using Windows.UI.Xaml.Navigation;
using Windows.Storage;
using System.IO;

namespace TacticalRadarFinal
{
    public sealed partial class RulerPage : Page
    {
        private XboxGameBarWidget widget;
        private DispatcherTimer timer;

        public RulerPage()
        {
            this.InitializeComponent();

            var localSettings = ApplicationData.Current.LocalSettings;
            if (localSettings.Values["ShowCrosshair"] is bool showCrosshair && showCrosshair)
            {
                CrosshairDot.Visibility = Visibility.Visible;
            }
            else
            {
                CrosshairDot.Visibility = Visibility.Collapsed;
            }

            timer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(50) };
            timer.Tick += UpdateRuler;
            timer.Start();
        }

        protected override void OnNavigatedTo(NavigationEventArgs e)
        {
            widget = e.Parameter as XboxGameBarWidget;
        }

        private async void CenterWidget_Click(object sender, RoutedEventArgs e) { if (widget != null) await widget.CenterWindowAsync(); }

        private void ToggleCrosshair_Click(object sender, RoutedEventArgs e)
        {
            bool isCurrentlyVisible = (CrosshairDot.Visibility == Visibility.Visible);

            if (isCurrentlyVisible)
            {
                CrosshairDot.Visibility = Visibility.Collapsed;
            }
            else
            {
                CrosshairDot.Visibility = Visibility.Visible;
            }

            ApplicationData.Current.LocalSettings.Values["ShowCrosshair"] = !isCurrentlyVisible;
        }

        private async void UpdateRuler(object sender, object e)
        {
            if (widget != null)
            {
                ControlPanel.Visibility = (widget.GameBarDisplayMode == XboxGameBarDisplayMode.Foreground)
                    ? Visibility.Visible : Visibility.Collapsed;
            }

            double pageHeight = this.ActualHeight;
            double cy = pageHeight / 2;
            double cx = this.ActualWidth / 2;

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

                // ==========================================
                // 【完美解绑】：各自独立读取开关状态
                // ==========================================
                bool isSiege = data.ContainsKey("siege") ? data.GetNamedBoolean("siege") : false;
                bool panzerOn = data.ContainsKey("panzer_on") ? data.GetNamedBoolean("panzer_on") : false;

                // 只要迫击炮 或 铁拳 有一个开着，就拉开画布幕布
                RulerCanvas.Visibility = (isSiege || panzerOn) ? Visibility.Visible : Visibility.Collapsed;

                // 两个都没开，直接退出，啥也不画
                if (!isSiege && !panzerOn) return;

                RulerCanvas.Children.Clear();

                // ==========================================
                // 1. 铁拳准星自动渲染逻辑 (只听 Y 键的)
                // ==========================================
                if (panzerOn && data.ContainsKey("panzer_data"))
                {
                    JsonArray panzerList = data.GetNamedArray("panzer_data");
                    foreach (IJsonValue item in panzerList)
                    {
                        JsonObject pObj = item.GetObject();
                        int m = (int)pObj.GetNamedNumber("m");
                        double drop1440 = pObj.GetNamedNumber("drop");
                        double dist = pObj.GetNamedNumber("dist");

                        // 【核心修复】：绕过 UWP 高度压缩，直接使用 Python 算出的物理绝对像素！
                        double actualY = cy + drop1440;

                        SolidColorBrush markerBrush = GetMarkerBrush(m);

                        Line pLine = new Line
                        {
                            X1 = cx - 30,
                            X2 = cx + 30,
                            Y1 = actualY,
                            Y2 = actualY,
                            Stroke = markerBrush,
                            StrokeThickness = 3
                        };
                        RulerCanvas.Children.Add(pLine);

                        TextBlock pLabel = new TextBlock
                        {
                            Text = $"{m + 1}号:{dist}m",
                            Foreground = markerBrush,
                            FontSize = 14,
                            FontWeight = FontWeights.Bold
                        };
                        Canvas.SetLeft(pLabel, cx + 35);
                        Canvas.SetTop(pLabel, actualY - 10);
                        RulerCanvas.Children.Add(pLabel);
                    }
                }

                // ==========================================
                // 2. 迫击炮标尺渲染逻辑 (只听 F8 或 F10 测距的)
                // ==========================================
                if (isSiege)
                {
                    // 画中心虚线
                    Line centerLine = new Line { X1 = cx, X2 = cx, Y1 = 0, Y2 = pageHeight, Stroke = new SolidColorBrush(Color.FromArgb(100, 255, 69, 0)), StrokeThickness = 1, StrokeDashArray = new DoubleCollection { 4, 4 } };
                    RulerCanvas.Children.Add(centerLine);

                    if (data.ContainsKey("ruler_data"))
                    {
                        JsonArray rulerData = data.GetNamedArray("ruler_data");
                        foreach (IJsonValue item in rulerData)
                        {
                            JsonObject obj = item.GetObject();
                            int m = (int)obj.GetNamedNumber("m");
                            int tick = (int)obj.GetNamedNumber("tick");
                            int dial = (int)obj.GetNamedNumber("dial");

                            double y = cy - (tick * 28.8);
                            if (y < 0 || y > pageHeight) continue;

                            SolidColorBrush markerColor = GetMarkerBrush(m);

                            Line line = new Line { X1 = cx - 12, X2 = cx + 12, Y1 = y, Y2 = y, Stroke = markerColor, StrokeThickness = 2 };
                            RulerCanvas.Children.Add(line);

                            double xPos = cx;
                            switch (m)
                            {
                                case 2: xPos = cx - 85; break;
                                case 0: xPos = cx - 45; break;
                                case 1: xPos = cx + 18; break;
                                case 3: xPos = cx + 55; break;
                                case 4: xPos = cx + 92; break;
                            }

                            TextBlock t = new TextBlock
                            {
                                Text = dial.ToString(),
                                FontSize = 12,
                                Foreground = markerColor,
                                FontWeight = FontWeights.Bold
                            };
                            Canvas.SetLeft(t, xPos);
                            Canvas.SetTop(t, y - 8);
                            RulerCanvas.Children.Add(t);
                        }
                    }
                }
            }
            catch { }
        }

        private SolidColorBrush GetMarkerBrush(int m)
        {
            if (m == 0) return new SolidColorBrush(Colors.Yellow);
            if (m == 1) return new SolidColorBrush(Color.FromArgb(255, 255, 69, 0));
            if (m == 2) return new SolidColorBrush(Color.FromArgb(255, 0, 119, 255));
            if (m == 4) return new SolidColorBrush(Colors.White); // 手动测距
            return new SolidColorBrush(Colors.Lime); // 默认绿色
        }
    }
}