/* Copyright (c) 2020 The Brave Authors. All rights reserved.
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http://mozilla.org/MPL/2.0/. */

#include "brave/components/ntp_background_images/browser/sponsored_images_component_data.h"

#include <optional>

#include "base/feature_list.h"
#include "brave/components/ntp_background_images/browser/features.h"
#include "build/build_config.h"

namespace ntp_background_images {

namespace {

constexpr SponsoredImagesComponentData kDemoData = {
    "DEMO",
    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAw+cUN/"
    "flbETi5zyjp4tRW4ustichzvFqeY4ayWpi/"
    "r+TwRgUaf0IyK2GYZF1xBsiuGO3B321ptcF7lpru32dxc2GUX7GLVHnYw+"
    "kM9bfw3WVqLPXVozCbyjqCW8IQXuUljOJ4tD9gJe8xvBeZ/"
    "WKg2K+7sYuhov6mcbBoUd4WLZW+89ryuBfZFi/4U6MX4Hemsw40Z3KHf/"
    "gAHpXXeU65Sqb8AhVMp0nckaX5u4vN09OTHLPAmCZmps5TcExoYwSPQaFK+6HrUV0/"
    "66Xw3kqo05CvN3bCC1UlDk3KAffg3LZ8u1E3gFcwK6xSjHYknGOuxabTVS6cNGECOEWKVs"
    "URwIDAQAB",
    "bejfdgcfgammhkbdmbaohoknehcdnbmn"};

// This list should be synced with the list of generateNTPSponsoredImages.js
// and packageNTPSponsoredImagesComponents.js in brave-core-crx-packager.
constexpr SponsoredImagesComponentData kRegionalData[] = {
#if BUILDFLAG(IS_ANDROID)
    {"TH",
     "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwyPIfrrssw5Lvn6sd2vAKb3Hc8gZ8bgCepFs/XInc0vzZCcT4IDxh+rcBhmCP5M2gHcTm4sU75G4gvna+HXAXS0eKuo6lP5vP8niaByaDPhcyHIDV3T83e5ZKJO8Ya+P48f4gUDaAiF/kj/TxARzyDOsZksk4jqpUEPI+7hWZM6sVSQli6zaW0YaLc3GgAru5Sz00ZzemyvcoCuTryGrYctdeyULymFFmMKLztCpsu0rqF3EHItjJrdxf8huH7d8sX7WCNMeTqcWXkaC7fCB2aOA5fAPCXMBrre/nSiWn5FvDfKYEEN0pYn2dyklIeT1OYjFTo2qjTPO5ntcfiKLHwIDAQAB",
     "jpkcofbbbanjjhkfejifehknaobcnjda"},
    {"VN",
     "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA9e5lHppK9M63RXIzZWt35obJQLunZD8i2oLqN3tNIf9H8TZM6UKMBaRERVfAIzcGp5R/5Umvr8MI6cOdt+dpkHcn8itUsTVKmvUGr3tGWcPstKqG6ppOjOTLDgzy9Xme4BfE8lP3kmV4BtTuuVyGcsqZC4ma89c/lZQDcqcSLzTIryHrNJG6gsPhy4iavnMBfY2luZuonxk4inb4AivrAn7ZuCCWiM4yLQOQlmceEhHaEM7qlTsQF7p0KDRMlz4XRWH0p16drw+h34IbQ0cJTMvIcEZYyhgK2UJYzMO4X2NhVv//WoN6RTHONYRndWQ3mFHvnulCm4s78B9rwExbywIDAQAB",
     "iflffbldgoppdiaimcakanhhljjggjkb"},
#elif BUILDFLAG(IS_IOS)
    {"TH",
     "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwyPIfrrssw5Lvn6sd2vAKb3Hc8gZ8bgCepFs/XInc0vzZCcT4IDxh+rcBhmCP5M2gHcTm4sU75G4gvna+HXAXS0eKuo6lP5vP8niaByaDPhcyHIDV3T83e5ZKJO8Ya+P48f4gUDaAiF/kj/TxARzyDOsZksk4jqpUEPI+7hWZM6sVSQli6zaW0YaLc3GgAru5Sz00ZzemyvcoCuTryGrYctdeyULymFFmMKLztCpsu0rqF3EHItjJrdxf8huH7d8sX7WCNMeTqcWXkaC7fCB2aOA5fAPCXMBrre/nSiWn5FvDfKYEEN0pYn2dyklIeT1OYjFTo2qjTPO5ntcfiKLHwIDAQAB",
     "jpkcofbbbanjjhkfejifehknaobcnjda"},
    {"VN",
     "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA9e5lHppK9M63RXIzZWt35obJQLunZD8i2oLqN3tNIf9H8TZM6UKMBaRERVfAIzcGp5R/5Umvr8MI6cOdt+dpkHcn8itUsTVKmvUGr3tGWcPstKqG6ppOjOTLDgzy9Xme4BfE8lP3kmV4BtTuuVyGcsqZC4ma89c/lZQDcqcSLzTIryHrNJG6gsPhy4iavnMBfY2luZuonxk4inb4AivrAn7ZuCCWiM4yLQOQlmceEhHaEM7qlTsQF7p0KDRMlz4XRWH0p16drw+h34IbQ0cJTMvIcEZYyhgK2UJYzMO4X2NhVv//WoN6RTHONYRndWQ3mFHvnulCm4s78B9rwExbywIDAQAB",
     "iflffbldgoppdiaimcakanhhljjggjkb"},
#else
    {"TH",
     "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwyPIfrrssw5Lvn6sd2vAKb3Hc8gZ8bgCepFs/XInc0vzZCcT4IDxh+rcBhmCP5M2gHcTm4sU75G4gvna+HXAXS0eKuo6lP5vP8niaByaDPhcyHIDV3T83e5ZKJO8Ya+P48f4gUDaAiF/kj/TxARzyDOsZksk4jqpUEPI+7hWZM6sVSQli6zaW0YaLc3GgAru5Sz00ZzemyvcoCuTryGrYctdeyULymFFmMKLztCpsu0rqF3EHItjJrdxf8huH7d8sX7WCNMeTqcWXkaC7fCB2aOA5fAPCXMBrre/nSiWn5FvDfKYEEN0pYn2dyklIeT1OYjFTo2qjTPO5ntcfiKLHwIDAQAB",
     "jpkcofbbbanjjhkfejifehknaobcnjda"},
    {"VN",
     "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA9e5lHppK9M63RXIzZWt35obJQLunZD8i2oLqN3tNIf9H8TZM6UKMBaRERVfAIzcGp5R/5Umvr8MI6cOdt+dpkHcn8itUsTVKmvUGr3tGWcPstKqG6ppOjOTLDgzy9Xme4BfE8lP3kmV4BtTuuVyGcsqZC4ma89c/lZQDcqcSLzTIryHrNJG6gsPhy4iavnMBfY2luZuonxk4inb4AivrAn7ZuCCWiM4yLQOQlmceEhHaEM7qlTsQF7p0KDRMlz4XRWH0p16drw+h34IbQ0cJTMvIcEZYyhgK2UJYzMO4X2NhVv//WoN6RTHONYRndWQ3mFHvnulCm4s78B9rwExbywIDAQAB",
     "iflffbldgoppdiaimcakanhhljjggjkb"},
#endif
};

}  // namespace

std::optional<SponsoredImagesComponentData> GetSponsoredImagesComponentData(
    const std::string& region) {
  if (base::FeatureList::IsEnabled(features::kBraveNTPBrandedWallpaperDemo)) {
    return kDemoData;
  }

  for (const auto& data : kRegionalData) {
    if (data.region == region) {
      return data;
    }
  }
  return std::nullopt;
}

}  // namespace ntp_background_images
