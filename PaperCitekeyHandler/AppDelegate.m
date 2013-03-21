//
//  AppDelegate.m
//  PaperCitekeyHandler
//
//  Created by Plantagenet on 21/03/13.
//  Copyright (c) 2013 Plantagenet. All rights reserved.
//

#import "AppDelegate.h"

@implementation AppDelegate

- (void)applicationWillFinishLaunching:(NSNotification *)aNotification
{
    // Insert code here to initialize your application
    [[NSAppleEventManager sharedAppleEventManager] setEventHandler:self
                                                    andSelector:@selector(handleURLEvent:withReplyEvent:)
                                                    forEventClass:kInternetEventClass
                                                    andEventID:kAEGetURL];

}


- (void)applicationDidFinishLaunching:(NSNotification *)notification
{
    [NSApp setServicesProvider:self];
    NSUpdateDynamicServices();
}

- (void)openCitekeyService:(NSPasteboard *)pboard
             userData:(NSString *)userData error:(NSString **)error {
    
    // Test for strings on the pasteboard.
    NSArray *classes = [NSArray arrayWithObject:[NSString class]];
    NSDictionary *options = [NSDictionary dictionary];
    
    if (![pboard canReadObjectForClasses:classes options:options]) {
        *error = NSLocalizedString(@"Error: couldn't open paper.",
                                   @"pboard couldn't give string.");
        return;
    }
    
    // Get and encrypt the string.
    NSString *pboardString = [pboard stringForType:NSPasteboardTypeString];
    NSLog(@"Got service citekey: %@", pboardString);

    [self openCitekey:pboardString];
}


- (void)handleURLEvent:(NSAppleEventDescriptor*)event withReplyEvent:(NSAppleEventDescriptor*)replyEvent
{
    NSString* url = [[event paramDescriptorForKeyword:keyDirectObject] stringValue];
    NSString* citekey = [[url componentsSeparatedByString:@"://"] lastObject];
    NSLog(@"Got citekey URL: %@", citekey);
    [self openCitekey:citekey];
}


- (void)openCitekey:(NSString*) citekey
{
    NSString *script_path = [[NSBundle mainBundle] pathForResource:@"open_citekey" ofType:@"py"];
    NSLog(@"Got handler: %@", script_path);
    
    NSTask *task;
    task = [[NSTask alloc] init];
    [task setLaunchPath: @"/usr/bin/python"];
    
    NSArray *arguments;
    arguments = [NSArray arrayWithObjects: script_path, citekey, nil];
    [task setArguments: arguments];
    
    NSPipe *pipe;
    pipe = [NSPipe pipe];
    [task setStandardError: pipe];
    [task setStandardOutput: pipe];
    
    NSFileHandle *file;
    file = [pipe fileHandleForReading];
    
    [task launch];
    [task waitUntilExit];
    
    NSData *data;
    data = [file readDataToEndOfFile];
    
    NSString *string;
    string = [[NSString alloc] initWithData: data encoding: NSUTF8StringEncoding];
    NSLog (@"Script returned (err/out):\n%@", string);
}

@end
