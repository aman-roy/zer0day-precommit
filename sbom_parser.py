import json
import subprocess
import os
import requests
import base64
import sys


BASE_URL = "https://api.zer0day.tech"

def is_opensource_license(license):
    # TODO: Add more licenses in future
    opensource_licenses = [
        "MIT", "Apache", "GPL", "BSD", "LGPL", "Mozilla",
        "Eclipse", "Creative Commons", "ISC", "Artistic",
        "Boost", "zlib", "Public Domain", "Unlicense"
    ]
    return any(lic.lower() in license.lower() for lic in opensource_licenses)

def check_github_repository(repo_url):
    # Example repo_url = pkg:github/octocat/Hello-World@1.0.0
    api_url = repo_url.replace("pkg:github", "https://api.github.com/repos")
    api_url = api_url.split("@")[0]
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            return not data.get('private', True)  # If 'private' is True, it's not open-source
    except:
        pass
    return False

def purl_to_url(purl):
    url = ""

    # TODO: Add support for more languages
    if purl.startswith('pkg:pypi'):
        package_name = re.search(r'pkg:pypi/(.+?)(?:@|$)', purl).group(1)
        url = f"https://pypi.org/pypi/{package_name}/json"
    elif purl.startswith('pkg:npm'):
        package_name = re.search(r'pkg:npm/(.+?)(?:@|$)', purl).group(1)
        url = f"https://registry.npmjs.org/{package_name}"
    elif purl.startswith('pkg:maven'):
        group, artifact = re.search(r'pkg:maven/(.+?)/(.+?)(?:@|$)', purl).groups()
        url = f"https://search.maven.org/solrsearch/select?q=g:{group}+AND+a:{artifact}&rows=1&wt=json"
    elif purl.startswith('pkg:nuget'):
        package_name = re.search(r'pkg:nuget/(.+?)(?:@|$)', purl).group(1)
        url = f"https://api.nuget.org/v3/registration5-semver1/{package_name.lower()}/index.json"
    elif purl.startswith('pkg:cargo'):
        package_name = re.search(r'pkg:cargo/(.+?)(?:@|$)', purl).group(1)
        url = f"https://crates.io/api/v1/crates/{package_name}"
    elif purl.startswith('pkg:composer'):
        vendor, package = re.search(r'pkg:composer/(.+?)/(.+?)(?:@|$)', purl).groups()
        url = f"https://packagist.org/packages/{vendor}/{package}.json"
    elif purl.startswith('pkg:golang'):
        package_name = re.search(r'pkg:golang/(.+?)(?:@|$)', purl).group(1)
        url = f"https://pkg.go.dev/{package_name}?tab=licenses"

    return url


def check_package_registry(purl):
    url = purl_to_url(purl)
    if url == "":
        return False

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'info' in data and 'license' in data['info']:
                return is_opensource_license(data['info']['license'])
            elif 'license' in data:
                return is_opensource_license(data['license'])
            elif 'items' in data and data['items']:
                return True  # Assume open-source if listed in Maven Central
            elif 'versions' in data:
                return True  # Assume open-source if listed in NuGet
            elif 'crate' in data:
                return True  # Assume open-source if listed on crates.io
            elif 'package' in data:
                return True  # Assume open-source if listed on Packagist
            elif 'tab=licenses' in url:
                return 'No license found' not in response.text
    except:
        pass
    return False

def is_likely_opensource(name, purl):
    if purl:
        # TODO: Add this check for other code platform for e.g. GitLab, bitbucket, SourceForge
        if purl.startswith("pkg:github"):
            return check_github_repository(purl)
        return check_package_registry(purl)
    
    return False

def parse_sbom(cyclonedx_file):
    with open(cyclonedx_file, 'r') as f:
        data = json.load(f)
    
    opensource_libs = []
    
    for component in data.get('components', []):
        name = component.get('name', '')
        version = component.get('version', '')
        purl = component.get('purl', '')
        url = component.get("externalReferences", [{}])[0].get("url", "No URL provided")

        licenses = component.get('licenses', [])
        
        is_opensource = False
        license_id = ''

        for license_info in licenses:
            if 'license' in license_info:
                license_id = license_info['license'].get('id', '')
                if is_opensource_license(license_id):
                    is_opensource = True
                    break
        
        if not is_opensource:
            is_opensource = is_likely_opensource(name, purl)
        
        if is_opensource:
            opensource_libs.append({
                'name': name,
                'version': version,
                'license': license_id if license_id else 'LIKELY_OPENSOURCE'
                'url': url if url == "NO URL provided" or url == "" else purl_to_url(purl)
            })
    
    return opensource_libs


def generate_sbom(output_file):
    print(f"Generating SBOM using Syft and saving to {output_file}...")
    try:
        subprocess.run(["syft", ".", "-o", "cyclonedx-json", f"--file={output_file}"], check=True)
        print("SBOM generated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error generating SBOM: {e}")
        exit(1)

def save_open_source_libraries_to_json(libraries, output_json_file):
    with open(output_json_file, 'w') as json_file:
        json.dump(libraries, json_file, indent=4)
    print(f"Open-source libraries saved to {output_json_file}")

def get_repo_name():
    return os.path.basename(os.getcwd())


def base64_encode_file(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def call_api(endpoint, json_data=None):
    # Get the API token from environment variables
    api_token = os.getenv("ZER0DAY_API_TOKEN")
    
    if not api_token:
        print("API token not found. Please set the ZER0DAY_API_TOKEN environment variable.")
        exit(1)

    url = f"{BASE_URL}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    if json_data:
        response = requests.post(url, headers=headers, json=json_data)
    else:
        response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text.strip()
    else:
        print(f"Error hitting endpoint {url}: {response.status_code}")
        exit(1)

def main():
    repo_name = get_repo_name()

    # Generate SBOM using Syft
    sbom_file = "sbom-output.json"  # Output path for SBOM file
    generate_sbom(sbom_file)

    # Parse SBOM and extract open-source libraries
    open_source_libraries = parse_sbom(sbom_file)
    output_json_file = "open_source_libraries.json"
    save_open_source_libraries_to_json(open_source_libraries, output_json_file)

    # Base64 encode the newly generated parsed JSON
    new_digest = base64_encode_file(output_json_file)

    # Get the last digest from the API
    last_digest = call_api(f"last-digest/{repo_name}")

    # Compare the base64 encodings
    if new_digest == last_digest:
        print("No changes in the SBOM from the last upload. Checking for vulnerabilities.")
        response = call_api(f"get-vulns/{repo_name}")
    else:
        print("Detected changes in the SBOM. Uploading new SBOM and checking for vulnerabilities.")
        response = call_api(f"upload-and-get-vulns/{repo_name}", json_data=open_source_libraries)

    # Process the response
    # The first line of the response will be an integer denoting how many bugs are found
    # Only a positive integer implies that there is a bug
    first_line = response.splitlines()[0]
    if first_line.isdigit() and int(first_line) > 0:
        print(f"Vulnerabilities found:\n{response}")
        sys.exit(1)  # Exit with 1 to block the commit
    else:
        print("No vulnerabilities found. Proceeding with commit.")
        sys.exit(0)  # Exit with 0 to allow the commit

if __name__ == "__main__":
    main()
