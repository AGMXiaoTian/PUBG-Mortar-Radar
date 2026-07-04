using System;
using System.Collections.Generic;
using Windows.ApplicationModel.Activation;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;
using Windows.UI.Xaml.Media;
using Microsoft.Gaming.XboxGameBar;

namespace TacticalRadarFinal
{
    sealed partial class App : Application
    {
        private Dictionary<string, XboxGameBarWidget> activeWidgets = new Dictionary<string, XboxGameBarWidget>();

        public App()
        {
            this.InitializeComponent();
        }

        protected override void OnActivated(IActivatedEventArgs args)
        {
            try
            {
                if (args.Kind == ActivationKind.Protocol)
                {
                    var protocolArgs = args as IProtocolActivatedEventArgs;
                    if (protocolArgs != null && protocolArgs.Uri.Scheme.Equals("ms-gamebarwidget"))
                    {
                        var widgetArgs = args as XboxGameBarWidgetActivatedEventArgs;
                        if (widgetArgs != null && widgetArgs.IsLaunchActivation)
                        {
                            var rootFrame = new Frame();

                            // 因为清单里已经授权了绝对透明，这里直接用 Transparent 即可！
                            rootFrame.Background = new SolidColorBrush(Windows.UI.Colors.Transparent);

                            Window.Current.Content = rootFrame;

                            var widget = new XboxGameBarWidget(widgetArgs, Window.Current.CoreWindow, rootFrame);
                            activeWidgets[widgetArgs.AppExtensionId] = widget;

                            if (widgetArgs.AppExtensionId == "CalculatorWidgetExt")
                            {
                                rootFrame.Navigate(typeof(MainPage), widget);
                            }
                            else if (widgetArgs.AppExtensionId == "RulerWidgetExt")
                            {
                                rootFrame.Navigate(typeof(RulerPage), widget);
                            }
                            Window.Current.Activate();
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                var errorFrame = new Frame();
                errorFrame.Background = new SolidColorBrush(Windows.UI.Colors.DarkRed);
                errorFrame.Content = new TextBlock() { Text = ex.ToString(), Foreground = new SolidColorBrush(Windows.UI.Colors.White), TextWrapping = TextWrapping.Wrap };
                Window.Current.Content = errorFrame; Window.Current.Activate();
            }
        }
    }
}