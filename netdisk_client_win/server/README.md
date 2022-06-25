# 修改一下server端的交流方式

const char* exceptions[] = {
    "login_accepted\n",
    "login_failed\n",

    "reg_accepted\n",
    "reg_failed\n",

    "upload_accepted\n",
    "upload_failed\n",
    "upload_completed\n",    // file transport complete

    "list_accepted\n",
    "list_failed\n",

    "move_accepted\n",
    "move_failed\n",

    "copy_accepted\n",
    "copy_failed\n",

    "remove_accepted\n",
    "remove_failed\n",

    "mkdir_accepted\n",
    "mkdir_failed\n",

    "rmdir_accepted\n",
    "rmdir_failed\n",

    "mvdir_accepted\n",
    "mvdir_failed\n",

    "download_accepted\n",
    "download_failed\n",

    "accepted\n",
    "failed\n"

};
