/* Copyright (c) 2020 The Brave Authors. All rights reserved.
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http://mozilla.org/MPL/2.0/. */

#include "brave/components/ntp_background_images/browser/ntp_background_images_component_installer.h"

#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#include "base/base64.h"
#include "base/containers/to_vector.h"
#include "base/functional/bind.h"
#include "brave/components/brave_component_updater/browser/brave_on_demand_updater.h"
#include "brave/components/ntp_background_images/browser/ntp_background_images_update_util.h"
#include "components/component_updater/component_installer.h"
#include "components/component_updater/component_updater_service.h"
#include "crypto/sha2.h"

using brave_component_updater::BraveOnDemandUpdater;

namespace ntp_background_images {

namespace {

constexpr char kNTPBIComponentPublicKey[] =
    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAoccKXaexU/+rYWkIbpr6b9+1"
    "eeJZ3+8DC+/LjPzRQO4Q4xp3bmcqNWH+7tV9m1YGVfJTeNznvfXN5f31Ec4J9b1lEeyX"
    "fNZPxjMsQArK/Lcp0J45J4IEKqsZmiBBmHabZTApoL9BowFFdlG1hdCgJjou10l2gAwW"
    "C3ZUwEos4K3ud+qVXB1H4Rbve/6XdzvknyMRq2KNEoMUIKMu4sRO9H+Fs+yXUap5zUsP"
    "hdVjZPTDftAhdjBdS8f0mFj09arhc58qkH9Pff2lUftJUscggrRU04OpSme0kDhnCP+2"
    "4VVt8FysnN9/JdkBEVsCSG8e9SX3gqL/ZQck12gGdORojQIDAQAB";  // NOLINT
constexpr char kNTPBIComponentID[] = "pjeihehgoeddbpfkelhjoniaiebjoak";

class NTPBackgroundImagesComponentInstallerPolicy
    : public component_updater::ComponentInstallerPolicy {
 public:
  explicit NTPBackgroundImagesComponentInstallerPolicy(
      const std::string& component_public_key,
      const std::string& component_id,
      const std::string& component_name,
      OnComponentReadyCallback callback);
  ~NTPBackgroundImagesComponentInstallerPolicy() override;

  NTPBackgroundImagesComponentInstallerPolicy(
      const NTPBackgroundImagesComponentInstallerPolicy&) = delete;
  NTPBackgroundImagesComponentInstallerPolicy& operator=(
      const NTPBackgroundImagesComponentInstallerPolicy&) = delete;

  // component_updater::ComponentInstallerPolicy
  bool SupportsGroupPolicyEnabledComponentUpdates() const override;
  bool RequiresNetworkEncryption() const override;
  update_client::CrxInstaller::Result OnCustomInstall(
      const base::Value::Dict& manifest,
      const base::FilePath& install_dir) override;
  void OnCustomUninstall() override;
  bool VerifyInstallation(const base::Value::Dict& manifest,
                          const base::FilePath& install_dir) const override;
  void ComponentReady(const base::Version& version,
                      const base::FilePath& path,
                      base::Value::Dict manifest) override;
  base::FilePath GetRelativeInstallDir() const override;
  void GetHash(std::vector<uint8_t>* hash) const override;
  std::string GetName() const override;
  update_client::InstallerAttributes GetInstallerAttributes() const override;
  bool IsBraveComponent() const override;

 private:
  const std::string component_id_;
  const std::string component_name_;
  OnComponentReadyCallback ready_callback_;
  std::array<uint8_t, crypto::kSHA256Length> component_hash_;
};

NTPBackgroundImagesComponentInstallerPolicy::
    NTPBackgroundImagesComponentInstallerPolicy(
        const std::string& component_public_key,
        const std::string& component_id,
        const std::string& component_name,
        OnComponentReadyCallback callback)
    : component_id_(component_id),
      component_name_(component_name),
      ready_callback_(std::move(callback)) {
  // Generate hash from public key.
  auto decoded_public_key = base::Base64Decode(component_public_key);
  CHECK(decoded_public_key);
  component_hash_ = crypto::SHA256Hash(*decoded_public_key);
}

NTPBackgroundImagesComponentInstallerPolicy::
~NTPBackgroundImagesComponentInstallerPolicy() = default;

bool NTPBackgroundImagesComponentInstallerPolicy::
    SupportsGroupPolicyEnabledComponentUpdates() const {
  return true;
}

bool NTPBackgroundImagesComponentInstallerPolicy::
    RequiresNetworkEncryption() const {
  return false;
}

update_client::CrxInstaller::Result
NTPBackgroundImagesComponentInstallerPolicy::OnCustomInstall(
    const base::Value::Dict& /*manifest*/,
    const base::FilePath& /*install_dir*/) {
  return update_client::CrxInstaller::Result(0);
}

void NTPBackgroundImagesComponentInstallerPolicy::OnCustomUninstall() {}

void NTPBackgroundImagesComponentInstallerPolicy::ComponentReady(
    const base::Version& /*version*/,
    const base::FilePath& path,
    base::Value::Dict /*manifest*/) {
  ready_callback_.Run(path);
}

bool NTPBackgroundImagesComponentInstallerPolicy::VerifyInstallation(
    const base::Value::Dict& /*manifest*/,
    const base::FilePath& /*install_dir*/) const {
  return true;
}

base::FilePath NTPBackgroundImagesComponentInstallerPolicy::
    GetRelativeInstallDir() const {
  return base::FilePath::FromUTF8Unsafe(component_id_);
}

void NTPBackgroundImagesComponentInstallerPolicy::GetHash(
    std::vector<uint8_t>* hash) const {
  *hash = base::ToVector(component_hash_);
}

std::string NTPBackgroundImagesComponentInstallerPolicy::GetName() const {
  return component_name_;
}

update_client::InstallerAttributes
NTPBackgroundImagesComponentInstallerPolicy::GetInstallerAttributes() const {
  return update_client::InstallerAttributes();
}

bool NTPBackgroundImagesComponentInstallerPolicy::IsBraveComponent() const {
  return true;
}

void RegisterNTPBackgroundImagesComponentCallback(
    const std::string& component_id) {
  BraveOnDemandUpdater::GetInstance()->EnsureInstalled(component_id);
}

void RegisterNTPSponsoredImagesComponentCallback(
    const std::string& component_id) {
  // Unlike other components that are only installed during registration,
  // we always update the sponsored images component upon registration.
  CheckAndUpdateSponsoredImagesComponent(component_id);
}

}  // namespace

void RegisterNTPBackgroundImagesComponent(
    component_updater::ComponentUpdateService* component_update_service,
    OnComponentReadyCallback callback) {
  if (!component_update_service) {
    // In test, `component_update_service` could be nullptr.
    return;
  }

  auto installer = base::MakeRefCounted<component_updater::ComponentInstaller>(
      std::make_unique<NTPBackgroundImagesComponentInstallerPolicy>(
          kNTPBIComponentPublicKey, kNTPBIComponentID, "NTP Background Images",
          std::move(callback)));
  installer->Register(
      component_update_service,
      base::BindOnce(&RegisterNTPBackgroundImagesComponentCallback,
                     kNTPBIComponentID));
}

void RegisterNTPSponsoredImagesComponent(
    component_updater::ComponentUpdateService* component_update_service,
    const std::string& component_public_key,
    const std::string& component_id,
    const std::string& component_name,
    OnComponentReadyCallback callback) {
  if (!component_update_service) {
    // In test, `component_update_service` could be nullptr.
    return;
  }

  auto installer = base::MakeRefCounted<component_updater::ComponentInstaller>(
      std::make_unique<NTPBackgroundImagesComponentInstallerPolicy>(
          component_public_key, component_id, component_name,
          std::move(callback)));
  installer->Register(
      component_update_service,
      base::BindOnce(&RegisterNTPSponsoredImagesComponentCallback,
                     component_id));
}

}  // namespace ntp_background_images
