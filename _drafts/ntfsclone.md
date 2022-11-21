





NTFSCLONE 是用于拷贝、保存、备份、恢复和挽救 NTFS的工具。

```
ntfsclone [OPTIONS] SOURCE
ntfsclone --save-image [OPTIONS] SOURCE
ntfsclone --restore-image [OPTIONS] SOURCE
ntfsclone --metadata [OPTIONS] SOURCE
```



## Options

Supported options are listed below. Most options have both single-letter and full-name forms. Multiple single-letter options that do not take an argument can be combined. For example, `-fv` is the equivalent of `-f` `-v`. A full-name option can be abbreviated to a unique prefix of its name.

- `-f`, `-–force`

  Forces `ntfsclone` to proceed, even if the filesystem is marked “dirty” following a consistency check.

- `-h`, `-–help`

  Show a list of options with a brief description of each one.

- `-i`, `-–ignore-fs-check`

  Ignore the result of the file system consistency check. This option can be used only with the `--meta-data` option. Any clusters that cause an inconsistency are saved.

- `-m`, `-–metadata`

  Clone only metadata. With this option, you must clone only to a file.

- `-o`, `-–output` file

  Clone NTFS to the non-existent file. If file is a hyphen (`-`), clone to the standard output.

- `-O`, `-–overwrite` file

  Clone NTFS to file, overwriting file if it already exists.

- `-–rescue`

  Ignore disk read errors so that a disk having bad sectors, for example, a failing disk, can be rescued with minimal impact on the disk. `ntfsclone` works at the lowest, sector level in this mode, enabling more data to be rescued. The contents of the unreadable sectors are filled with the question mark (`?`) character; the beginning of such sectors are marked by the string: `BadSector`.

- `-r`, `-–restore-image` source

  Restore from the special image format specified by source. If source is a hyphen (`-`), the image is read from the standard input.

- `-s`, `-–save-image`

  Save to the special image format. In terms of space usage and speed, this is the most efficient option if imaging is done to the standard output. This option is useful for image compression, encryption, or streaming through a network.

## Examples

**Example 1 Cloning with Overwrite Option**

The following command clones with the `-–overwrite` option.

```
# ntfsclone --overwrite /dev/dsk/c0d2p1 /dev/dsk/c0d0p1
```

**Example 2 Saving to Special Image Format**

The following command clones to the special image format to its original partition.

```
# ntfsclone --save-image --output backup.img /dev/dsk/c0d0p1
```

**Example 3 Restoring from a Special Image File**

The following command restores an NTFS from a special image file.

```
# ntfsclone --restore-image --overwrite /dev/dsk/c0d0p1 backup.img
```

**Example 4 Saving to a Compressed Image**

The following command saves an NTFS to a compressed image file.

```
# ntfsclone --save-image -o - /dev/dsk/c0d0p1
```

**Example 5 Restoring from a Compressed Image**

The following command restores an NTFS volume from a compressed image file.

```
# gunzip -c backup.img.gz | \
ntfsclone --restore-image --overwrite /dev/dsk/c0d0p1 -
```

**Example 6 Backing up to a Remote Host Using ssh**

The following command backs up to a remote host, using [`ssh`(1)](https://docs.oracle.com/cd/E23824_01/html/821-1461/ssh-1.html#REFMAN1ssh-1). Note that `ssh` will probably require a password.

```
# ntfsclone --save-image --output - /dev/dsk/c0d0p1 | \
gzip -c | ssh host `cat > backup.img.gz`
```

**Example 7 Restoring from a Remote Host Using ssh**

The following command restores from a remote host, using [`ssh`(1)](https://docs.oracle.com/cd/E23824_01/html/821-1461/ssh-1.html#REFMAN1ssh-1). Note that `ssh` will probably require a password.

```
# ssh host `cat backup.img.gz` | gunzip -c | \
ntfsclone --restore-image --overwrite /dev/dsk/c0d0p1 -
```

**Example 8 Streaming an Image File from a Web Server**

The following command streams an image file from a web server and restore it to a partition.

```
# wget -qO - http://server/backup.img | \
ntfsclone --restore-image --overwrite /dev/dsk/c0d0p1 -
```

**Example 9 Cloning to a New File**

The following command clones an NTFS volume to a non-existent file.

```
# ntfsclone --output ntfs-clone.img /dev/dsk/c0d0p1
```

**Example 10 Packing NTFS Metadata**

The following command packs NTFS metadata into an image file. Note that `bzip2` takes a much longer time than `gzip`, but produces an archive that is up to ten times smaller than the latter produces.

```
# ntfsclone --metadata --output ntfsmeta.img /dev/dsk/c0d0p1
bzip2 ntfsmeta.img
```

**Example 11 Unpacking NTFS Metadata**

The following command unpacks NTFS metadata into a sparse file.

```
# bunzip2 -c ntfsmeta.img.bz2 | \
cp --sparse=always /proc/self/fd/0 ntfsmeta.img
```

## Exit Status

The return code is zero on success, non-zero otherwise.